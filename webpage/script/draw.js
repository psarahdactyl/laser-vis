var hitSegment, path, activePath, selectionRectangle;
var movePath = false;
var drawing = null;

var hitOptions = {
	segments: true,
	stroke: true,
	fill: true,
	tolerance: 10,
	bounds: true,
	handles: true

};

function initSelectionRectangle(shape) {
    if(selectionRectangle)
        selectionRectangle.remove();
    var reset = shape.rotation==0 && shape.scaling.x==1 && shape.scaling.y==1;
    var bounds;
    if(reset)
    {
        console.log('reset');
        bounds = shape.bounds;
        shape.pInitialBounds = shape.bounds;
    }
    else
    {
        console.log('no reset');
        bounds = shape.pInitialBounds;
    }
    console.log('bounds: ' + bounds);
    b = bounds.clone().expand(10,10);

    selectionRectangle = new Path.Rectangle(b);
    selectionRectangle.pivot = selectionRectangle.position;
    selectionRectangle.insert(2, new Point(b.center.x, b.top));
    selectionRectangle.insert(2, new Point(b.center.x, b.top-25));
    selectionRectangle.insert(2, new Point(b.center.x, b.top));
    if(!reset)
    {
        selectionRectangle.position = shape.bounds.center;
        selectionRectangle.rotation = shape.rotation;
        selectionRectangle.scaling = shape.scaling;
    }

    selectionRectangle.strokeWidth = 1;
    selectionRectangle.strokeColor = 'blue';
    selectionRectangle.name = "selection rectangle";
    selectionRectangle.selected = true;
    selectionRectangle.ppath = shape;
    selectionRectangle.ppath.pivot = selectionRectangle.pivot;
}

function onMouseDown(event) {
	hitSegment = null;
	var hitResult = project.hitTest(event.point, hitOptions);

	if(!drawing)
		drawing = new Drawing([]);

	if(path)
		path.selected = false;

	if (event.modifiers.shift) {
		activePath = null;
		console.log('drawing line');
		path = new Path({
			segments: [event.point],
			strokeColor: '#351909',
			strokeWidth: 5,
			// Select the path, so we can see its segment points:
			fullySelected: true
		}); 
		path.simplify(7);
		drawing.addToDrawing(path);
	}

	if (hitResult) {
		if (activePath)
			activePath.selected = false;
		if (hitResult.item !== selectionRectangle) 
			activePath = hitResult.item;
		activePath.fullySelected = true;
		if (hitResult.type == 'segment') {
			hitSegment = hitResult.segment;
			activePath = hitSegment;
			initSelectionRectangle(activePath);
		} else if (hitResult.type == 'stroke') {
			var location = hitResult.location;
			hitSegment = activePath;//.insert(location.index + 1, event.point);
			activePath = hitSegment;
			initSelectionRectangle(activePath);
		} else if (hitResult.type == 'bounds') {
			var location = hitResult.location;
			console.log(hitResult.bounds);
			hitSegment = hitResult.bounds;

		}
		project.activeLayer.addChild(hitResult.item);

	} else {
		hitSegment = null;
		console.log('nothing hit');
		if (activePath) {
			activePath.selected = false;
			activePath = null;
		}
		if (selectionRectangle) {
			selectionRectangle.selected = false;
			selectionRectangle.remove();
			selectionRectangle = null;
		}
	}
	
}

/*
function onMouseMove(event) {
	project.activeLayer.selected = false;
	if (event.item)
		event.item.selected = true;
}
*/

function onMouseDrag(event) {
	if (event.modifiers.shift && path){
		path.add(event.point);
	}
	
	if (hitSegment) {
		hitSegment.point += event.delta;
		//activePath.smooth();
	} else if (activePath) {
		activePath.position += event.delta;
		initSelectionRectangle(activePath);
	}
}

function onKeyDown(event) {
	 if((event.key == 'delete') && activePath) {
	 	drawing.deleteFromDrawing(activePath);
        activePath.remove();
        if (selectionRectangle)
        	selectionRectangle.remove();
     }
     else if(event.key == 'control' && event.character == 'z') {
     	drawing.deleteFromHistory(drawing.getLastAction());
     }
}

function onMouseUp(event) {
	if(path) {
		//path.simplify(7);
		path.smooth();
		var canvas = document.getElementById("drawingCanvas");
		var canvasData = canvas.toDataURL();
		sendBackNormals(canvasData);
		sendBackExplode(canvasData);

	}
	if (activePath) {
		activePath.fullySelected = true;
		//activePath.simplify(2);
		activePath.smooth();
	} 
	if(selectionRectangle) {
        selectionRectangle.selected = true;

	}



 //    var capture = project.exportSVG();

 //    THREE.SVGLoader = function ( manager ) {
	// 	this.manager = ( manager !== undefined ) ? manager : THREE.DefaultLoadingManager;
	// };

	// THREE.SVGLoader.prototype = {
	// 	constructor: THREE.SVGLoader,
	// 	load: function ( url, onLoad, onProgress, onError ) {
	// 		var scope = this;
	// 		var parser = new DOMParser();
	// 		var loader = new THREE.FileLoader( scope.manager );
	// 		loader.load( capture );
	// 	}
	// };

}