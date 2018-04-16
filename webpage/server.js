// Dependencies
var express = require("express"),
    fs = require("fs"),
    rimraf = require("rimraf"),
    mkdirp = require("mkdirp"),
    bodyParser = require("body-parser"),
    multer  = require('multer'),
    storage = multer.diskStorage({
      destination: function (req, file, cb) {
        cb(null, __dirname + "/server/uploads/")
      },
      filename: function (req, file, cb) {
        cb(null, file.originalname)
      }
    }),
    upload = multer({ storage : storage }),
    app = express(),

    // paths/constants
    fileInputName = process.env.FILE_INPUT_NAME || "file",
    publicDir = process.env.PUBLIC_DIR || __dirname,
    nodeModulesDir = process.env.NODE_MODULES_DIR || __dirname + "/node_modules/",
    uploadedFilesPath = process.env.UPLOADED_FILES_DIR || __dirname + "\\server\\uploads\\",
    chunkDirName = "chunks",
    port = process.env.SERVER_PORT || 8080,
    maxFileSize = process.env.MAX_FILE_SIZE || 0; // in bytes, 0 for unlimited

var pythonProcessor = require('./script/server-side/make3DAssets')


// routes
app.use(express.static(publicDir));
app.post("/server/uploads/", upload.single("svg"), onUpload);
app.use(nodeModulesDir, express.static(nodeModulesDir));
app.delete("/uploads/:uuid", onDeleteFile);
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());

//http://localhost:8080/datafromcanvas
app.post("/datafromcanvas", function(req, res) {
    //get your canvasDataUrl here from the req object
    var myUrlData = req("canvasDataUrl");
    pythonProcessor.processImageInPython(myUrlData);
});


app.listen(port, function(){
    console.log('Server running on 8080... ');
});

function onUpload(req, res, next) {
    //console.log(req.file);
    if (!req.file)
        return res.status(400).send('No files were uploaded.');
     
    var svg = req.file;
    console.log(svg);

    //res.send('File uploaded!');
    
}

function onSimpleUpload(fields, file, res) {
    console.log('Simple upload');
    var uuid = fields.qquuid,
        responseData = {
            success: false
        };

    file.name = fields.qqfilename;

    if (isValid(file.size)) {
        moveUploadedFile(file, uuid, function() {
                responseData.success = true;
                res.send(responseData);
            },
            function() {
                responseData.error = "Problem copying the file!";
                res.send(responseData);
            });
    }
    else {
        failWithTooBigFile(responseData, res);
    }
}

function onChunkedUpload(fields, file, res) {
    var size = parseInt(fields.qqtotalfilesize),
        uuid = fields.qquuid,
        index = fields.qqpartindex,
        totalParts = parseInt(fields.qqtotalparts),
        responseData = {
            success: false
        };

    file.name = fields.qqfilename;

    if (isValid(size)) {
        storeChunk(file, uuid, index, totalParts, function() {
            if (index < totalParts - 1) {
                responseData.success = true;
                res.send(responseData);
            }
            else {
                combineChunks(file, uuid, function() {
                        responseData.success = true;
                        res.send(responseData);
                    },
                    function() {
                        responseData.error = "Problem combining the chunks!";
                        res.send(responseData);
                    });
            }
        },
        function(reset) {
            responseData.error = "Problem storing the chunk!";
            res.send(responseData);
        });
    }
    else {
        failWithTooBigFile(responseData, res);
    }
}

function failWithTooBigFile(responseData, res) {
    responseData.error = "Too big!";
    responseData.preventRetry = true;
    res.send(responseData);
}

function onDeleteFile(req, res) {
    var uuid = req.params.uuid,
        dirToDelete = uploadedFilesPath + uuid;

    rimraf(dirToDelete, function(error) {
        if (error) {
            console.error("Problem deleting file! " + error);
            res.status(500);
        }

        res.send();
    });
}

function isValid(size) {
    return maxFileSize === 0 || size < maxFileSize;
}

function moveFile(destinationDir, sourceFile, destinationFile, success, failure) {
    mkdirp(destinationDir, function(error) {
        var sourceStream, destStream;

        if (error) {
            console.error("Problem creating directory " + destinationDir + ": " + error);
            failure();
        }
        else {
            sourceStream = fs.createReadStream(sourceFile);
            destStream = fs.createWriteStream(destinationFile);

            sourceStream
                .on("error", function(error) {
                    console.error("Problem copying file: " + error.stack);
                    destStream.end();
                    failure();
                })
                .on("end", function(){
                    destStream.end();
                    success();
                })
                .pipe(destStream);
        }
    });
}

function moveUploadedFile(file, uuid, success, failure) {
    var destinationDir = uploadedFilesPath + uuid + "/",
        fileDestination = destinationDir + file.name;

    moveFile(destinationDir, file.path, fileDestination, success, failure);
}

function storeChunk(file, uuid, index, numChunks, success, failure) {
    var destinationDir = uploadedFilesPath + uuid + "/" + chunkDirName + "/",
        chunkFilename = getChunkFilename(index, numChunks),
        fileDestination = destinationDir + chunkFilename;

    moveFile(destinationDir, file.path, fileDestination, success, failure);
}

function combineChunks(file, uuid, success, failure) {
    var chunksDir = uploadedFilesPath + uuid + "/" + chunkDirName + "/",
        destinationDir = uploadedFilesPath + uuid + "/",
        fileDestination = destinationDir + file.name;


    fs.readdir(chunksDir, function(err, fileNames) {
        var destFileStream;

        if (err) {
            console.error("Problem listing chunks! " + err);
            failure();
        }
        else {
            fileNames.sort();
            destFileStream = fs.createWriteStream(fileDestination, {flags: "a"});

            appendToStream(destFileStream, chunksDir, fileNames, 0, function() {
                rimraf(chunksDir, function(rimrafError) {
                    if (rimrafError) {
                        console.log("Problem deleting chunks dir! " + rimrafError);
                    }
                });
                success();
            },
            failure);
        }
    });
}

function appendToStream(destStream, srcDir, srcFilesnames, index, success, failure) {
    if (index < srcFilesnames.length) {
        fs.createReadStream(srcDir + srcFilesnames[index])
            .on("end", function() {
                appendToStream(destStream, srcDir, srcFilesnames, index + 1, success, failure);
            })
            .on("error", function(error) {
                console.error("Problem appending chunk! " + error);
                destStream.end();
                failure();
            })
            .pipe(destStream, {end: false});
    }
    else {
        destStream.end();
        success();
    }
}

function getChunkFilename(index, count) {
    var digits = new String(count).length,
        zeros = new Array(digits + 1).join("0");

    return (zeros + index).slice(-digits);
}