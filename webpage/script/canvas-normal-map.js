requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: '../node_modules',
});


function createNormalMap() {

var moduleName = 'python-shell';
require([moduleName], function(PythonShell){
    var canvas = document.getElementById('drawingCanvas');
	var dataURL = canvas.toDataURL();

	var options = {
	  mode: 'binary',
	  pythonPath: 'C:/Anaconda3/Scripts',
	  scriptPath: '/python/',
	  args: [dataURL]
	};
	 
	PythonShell.run('normalMap.py', options, function (err, results) {
	  if (err) throw err;
	  // results is an array consisting of messages collected during execution
	  console.log('results: %j', results);
	});

})

//var PythonShell = require('python-shell');
};
