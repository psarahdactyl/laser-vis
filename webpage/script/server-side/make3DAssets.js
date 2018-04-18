var PythonShell = require('python-shell');

exports.normalMapInPython = function (dataAsBigAssUrl) {
	var arg = dataAsBigAssUrl['canvasImage'];

		var options = {
		  pythonPath: 'C:/Anaconda3/python.exe',
		  scriptPath: './script/python/',
		  pythonOptions: ['-u']
		};

	pyshell = new PythonShell('normalMap.py', options);
	pyshell.send(arg)
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
		  pythonPath: 'C:/Anaconda3/python.exe',
		  scriptPath: './script/python/',
		  pythonOptions: ['-u']
		};


	pyshell = new PythonShell('explode.py', options);
	//pyshell.stdin.write(arg);
	pyshell.send(arg);

	pyshell.on('message', function (message) {
  		// received a message sent from the Python script (a simple "print" statement)
  		console.log(message);
	});

	pyshell.end(function (err,code,signal) {
	if (err) throw err;
	  console.log('The exit code was: ' + code);
	  console.log('The exit signal was: ' + signal);
	  console.log('finished explode alpha maps');
	});	

};
