var PythonShell = require('python-shell');

exports.normalMapInPython = function (dataAsBigAssUrl) {
	var arg = dataAsBigAssUrl['canvasImage'];

		var options = {
		  mode: 'binary',
		  pythonPath: 'C:/Anaconda3/python.exe',
		  scriptPath: __dirname + '/../python/',
		  //args: [arg]
		};

	pyshell = new PythonShell('normalMap.py', options);
	pyshell.stdin.write(arg);
	//console.log(arg);
	pyshell.end(function (err,code,signal) {
	if (err) throw err;
	  console.log('The exit code was: ' + code);
	  console.log('The exit signal was: ' + signal);
	  console.log('finished normal/displacement maps');
	});	
};


exports.explodeInPython = function (dataAsBigAssUrl) {
	var arg = dataAsBigAssUrl['canvasImage'];

		var options = {
		  mode: 'binary',
		  pythonPath: 'C:/Anaconda3/python.exe',
		  scriptPath: __dirname + '/../python/',
		  //args: [arg]
		};

	pyshell = new PythonShell('explode.py', options);
	pyshell.stdin.write(arg);
	//console.log(arg);
	pyshell.end(function (err,code,signal) {
	if (err) throw err;
	  console.log('The exit code was: ' + code);
	  console.log('The exit signal was: ' + signal);
	  console.log('finished explode alpha maps');
	});	
};
