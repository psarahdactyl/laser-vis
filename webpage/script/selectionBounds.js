class SelectionBounds {
    constructor()


}


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