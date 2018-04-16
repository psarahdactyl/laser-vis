var PythonShell = require('python-shell');

exports.processImageInPython = function (dataAsBigAssUrl) {

		var options = {
		  mode: 'binary',
		  pythonPath: 'C:/Anaconda3/Scripts',
		  scriptPath: '/python/',
		  args: [dataAsBigAssURL]
		};

	PythonShell.run('normalMap.py', options, function (err, results) {
		if (err) throw err;
		// results is an array consisting of messages collected during execution
		console.log('results: %j', results);
	});	
};

