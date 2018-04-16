
function sendBack(canvasData) {
	
	$.ajax({
        url: '/datafromcanvas',
        type: 'post',
        data: {'canvasImage': canvasData}
    });

}