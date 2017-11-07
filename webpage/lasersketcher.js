var x = 100;
var y = 100;
var angle1 = 0.0;
var segLength = 50;


setup();
draw();

function setup() {
  var canvas = createCanvas(850, 500);
  canvas.parent("p5container");
  background(255);
  strokeWeight(20.0);
  stroke(0, 100);
}

function draw() {
  stroke(0);
  if (mouseIsPressed == true) {
    line(mouseX, mouseY, pmouseX, pmouseY);
  
  var dx = mouseX - x;
  var dy = mouseY - y;
  angle1 = atan2(dy, dx);  
  x = mouseX - (cos(angle1) * segLength);
  y = mouseY - (sin(angle1) * segLength);
 
  segment(x, y, angle1); 
  ellipse(x, y, 20, 20);
}

function segment(x, y, a) {
  push();
  translate(x, y);
  rotate(a);
  line(0, 0, segLength, 0);
  pop();
}
