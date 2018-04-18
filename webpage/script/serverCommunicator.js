
function sendBackNormals(canvasDataUrl) {
	
	$.ajax({
        url: '/canvastonormals',
        type: 'post',
        data: {'canvasImage': canvasDataUrl}
    });

}

function sendBackExplode(canvasDataUrl) {
	
	$.ajax({
        url: '/canvastoexplode',
        type: 'post',
        data: {'canvasImage': canvasDataUrl}
    });

}