// canvas settings
var viewWidth = 460,
    viewHeight = 685,
    drawingCanvas = document.getElementById("renderCanvas"),
    ctx,
    timeStep = (1/60),
    time = 0;
// texture and normal data
var textureDiffuseImageData,
    textureNormalImageData,
    textureColors = new Float32Array(viewWidth * viewHeight * 4),
    textureNormals = new Float32Array(viewWidth * viewHeight * 4),
    outputImageData;
// ambient light illuminates all pixels equally
// each color channel(red, green, blue, alpha) is stored in range 0 to 1
// the intensity is determined by alpha
var ambientLight = {
    r:1,
    g:1,
    b:1,
    a:0.2
};
// point light will emit light from a position in all directions
var pointLight = {
    // color
    r:1,
    g:1,
    b:1,
    a:1,
    // position
    x:0,
    y:0,
    z:64,
    // attenuation
    // this reduces the light luminance based on distance
    radius:256,
    attenuateDistance:function(distance) {
        var f = distance / this.radius;

        return 1 / (f * f);
    }
};

function initDrawingCanvas() {
    drawingCanvas.width = viewWidth;
    drawingCanvas.height = viewHeight;
    ctx = drawingCanvas.getContext('2d');
}

function initTextures() {
    var textureW = 460,
        textureH = 685,
        data;

    // get the pixel colors of the texture
    // this would be the color of the output pixel without any lighting
    ctx.drawImage(texture_img, 0, 0);
    textureDiffuseImageData = ctx.getImageData(0, 0, textureW, textureH);
    data = textureDiffuseImageData.data;

    // imageData.data is an array of colors
    // colors are stored as int values between 0 and 255
    // 4 consecutive indices represent the colors of a pixel (red, green, blue, alpha)
    // we will store the pixel colors as floats in range of 0 to 1
    // these will be used in the lighting calculations
    for (var i = 0; i < data.length; i += 4) {
        textureColors[i + 0] = data[i + 0] / 255; // red
        textureColors[i + 1] = data[i + 1] / 255; // green
        textureColors[i + 2] = data[i + 2] / 255; // blue
        textureColors[i + 3] = 1;                 // alpha
    }

    // get the pixel colors of the normal map
    // normals (x, y, z) are stored in colors (r, g, b)
    ctx.drawImage(texture_normal_img, 0, 0);
    textureNormalImageData = ctx.getImageData(0, 0, textureW, textureH);
    data = textureNormalImageData.data;

    for (var j = 0; j < data.length; j += 4) {

        // normals must be converted to a range of -1 to 1
        var x = (data[j + 0] / 255) * 2 - 1,
            y = (data[j + 1] / 255) * 2 - 1,
            z = (data[j + 2] / 255) * 2 - 1,
            l = length(x, y, z);

        // they must also be normalised, go get the surface normal direction
        textureNormals[j + 0] = x / l;
        textureNormals[j + 1] = y / l;
        textureNormals[j + 2] = z / l;
    }

    // create empty output data, which will be drawn to the canvas
    outputImageData = ctx.createImageData(textureW, textureH);
}

function loop() {
    update();
    draw();
    time += timeStep;
    requestAnimationFrame(loop);
}

function update() {
    // move the point light
    if (followMouse === true) {
        var mouse = getMousePosition();
        pointLight.x = mouse.x;
        pointLight.y = mouse.y;
    }
    else {
        pointLight.x = 256 + Math.sin(time) * 192;
        pointLight.y = 256 + Math.cos(time) * 192;
    }

    // the code below will determine the color of every pixel on screen

    var diffuse = textureColors,
        normals = textureNormals,
        output = outputImageData.data;

    for (var i = 0; i < output.length; i+=4) {
        // get the pixel color from the texture. This is the diffuse color.
        var diffuseR = diffuse[i + 0],
            diffuseG = diffuse[i + 1],
            diffuseB = diffuse[i + 2];
        // get the corresponding normal from the normal map
        var normalX = normals[i + 0],
            normalY = normals[i + 1],
            normalZ = normals[i + 2];
        // get screen space position (x, y)
        var fragmentX = (i / 4) % viewWidth,
            fragmentY = (i / 4 / viewWidth) >> 0, // bitwise Math.floor
            // determine distance to the point light
            lightDirX = pointLight.x - fragmentX,
            lightDirY = pointLight.y - fragmentY,
            lightDirZ = pointLight.z,
            lightDist = length(lightDirX, lightDirY, lightDirZ);
        // normalize distance to get direction
        lightDirX /= lightDist;
        lightDirY /= lightDist;
        lightDirZ /= lightDist;

        // dot product of light direction and surface normal (the direction that pixel of surface is 'pointing')
        // negative values indicate that the pixel is pointing away from the light, so it will not be illuminated (clamped to 0)
        // positive values indicate that teh pixel is pointing towards the light, so it be illuminated based on the angle (0 to 1)
        var dp = dot(lightDirX, lightDirY, lightDirZ, normalX, normalY, normalZ);
        var reflection = dp < 0 ? 0 : dp;
        // this will reduce the effect of the point light based on distance
        var attenuation = pointLight.attenuateDistance(lightDist);
        // this is the effect of the point light on this pixel
        var pointR = pointLight.r * pointLight.a * reflection * attenuation,
            pointG = pointLight.g * pointLight.a * reflection * attenuation,
            pointB = pointLight.b * pointLight.a * reflection * attenuation;
        // this is the effect of the ambient light on this pixel (same for all pixels)
        var ambientR = ambientLight.r * ambientLight.a,
            ambientG = ambientLight.g * ambientLight.a,
            ambientB = ambientLight.b * ambientLight.a;
        // final color = texture color * (ambient light color + point light color)
        // the color must be in 0 to 255 range
        output[i + 0] = diffuseR * (ambientR + pointR) * 255; // red
        output[i + 1] = diffuseG * (ambientG + pointG) * 255; // green
        output[i + 2] = diffuseB * (ambientB + pointB) * 255; // blue
        output[i + 3] = 255;                                  // alpha
    }
}

function draw() {
    // render the processed image data onto the canvas
    ctx.putImageData(outputImageData, 0, 0);

    // show light position
    if (showPointLight === true) {
        ctx.fillStyle = '#f0f';
        ctx.beginPath();
        ctx.arc(pointLight.x, pointLight.y, 5, 0, Math.PI * 2);
        ctx.fill();
    }
}

// vector dot product
function dot(x1, y1, z1, x2, y2, z2) {
    return x1 * x2 + y1 * y2 + z1 * z2;
}
// vector length
function length(x, y, z) {
    return Math.sqrt(x*x + y*y + z*z);
}

// GUI
var showPointLight = true;
var followMouse = false;

function initGUI() {
    var gui = new dat.GUI();

    var ambientFolder = gui.addFolder('ambient light');
    ambientFolder.add(ambientLight, 'r', 0, 1).name('red');
    ambientFolder.add(ambientLight, 'g', 0, 1).name('green');
    ambientFolder.add(ambientLight, 'b', 0, 1).name('blue');
    ambientFolder.add(ambientLight, 'a', 0, 1).name('intensity');

    var pointFolder = gui.addFolder('point light');
    pointFolder.add(pointLight, 'r', 0, 1).name('red');
    pointFolder.add(pointLight, 'g', 0, 1).name('green');
    pointFolder.add(pointLight, 'b', 0, 1).name('blue');
    pointFolder.add(pointLight, 'a', 0, 1).name('intensity');
    pointFolder.add(pointLight, 'radius', 0, 512).name('radius');
    pointFolder.add(pointLight, 'z', 0, 512).name('distance');

    gui.add(window, 'showPointLight').name('show point light');
    gui.add(window, 'followMouse').name('follow mouse');
}

// get mouse position within the canvas
getMousePosition = function() {
    var mouseX,
        mouseY,
        rect = drawingCanvas.getBoundingClientRect();

    drawingCanvas.addEventListener('mousemove', function(e) {
        mouseX = event.clientX - rect.left;
        mouseY = event.clientY - rect.top;
    });

    return function() {
        return {x:mouseX, y:mouseY};
    };
}();

// load images

var imagesLoaded = 0;
var texture_img = new Image();
var texture_normal_img = new Image();

function imageLoadedHandler() {
    if (++imagesLoaded === 2) {
        initDrawingCanvas();
        initTextures();
        initGUI();
        requestAnimationFrame(loop);
    }
}

texture_img.crossOrigin = "Anonymous";
texture_img.onload = imageLoadedHandler;
texture_img.src = '../../normal-mapping/test.JPG';
texture_normal_img.crossOrigin = "Anonymous";
texture_normal_img.onload = imageLoadedHandler;
texture_normal_img.src = '../../normal-mapping/normal.png';