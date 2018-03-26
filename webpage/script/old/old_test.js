var laserView = {
	camera: new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 500, 10000 ),
	material: new THREE.MeshPhongMaterial(),
	scene: new THREE.Scene(),
	loader: new THREE.TextureLoader(),
	renderCanvas: document.getElementById("renderCanvas"),
	renderer: new THREE.WebGLRenderer( { canvas:renderCanvas } ),
	get orbit () {return new THREE.OrbitControls( this.camera, this.renderer.domElement );}
};

// canvas settings
var canvasSettings = {
    viewWidth: laserView.renderCanvas.clientWidth,
    viewHeight: laserView.renderCanvas.clientHeight
};

var animationSettings = {
    timeStep: (1/60),
    time: 0
};


function initCamera() {
    laserView.camera.position.set( 0, 0, 2500 );
    
    laserView.scene.background = new THREE.Color( 0xf0f0f0 );

    //var drawingCanvas = document.getElementById("drawingCanvas");

    // load a resource
    var texture = laserView.loader.load(
        // resource URL
        /*drawingCanvas.dataURL()*/
        "../img/Birch-Plywood-Cut.jpg");

    var normal = laserView.loader.load("../img/Birch-Plywood-Cut.jpg_normal.png");
    var displacement = laserView.loader.load("../img/Birch-Plywood-Cut.jpg_displacement.png");

    laserView.material.map = texture;
    laserView.normalMap = normal;
    laserView.displacementMap = displacement;
    laserView.displacementScale = 10;
    laserView.displacementBias = -0.5;
    laserView.specular = 15;

    plane = new THREE.Mesh(
    	new THREE.BoxGeometry(laserView.renderCanvas.clientHeight, laserView.renderCanvas.clientWidth,1, 100, 100, 5), 
    	laserView.material);
    plane.material.needsUpdate = true; // update material
    plane.receiveShadow = true;
    
    laserView.scene.add( plane );
        
    //renderer = new THREE.WebGLRenderer( { canvas:renderCanvas } );
    laserView.renderer.setPixelRatio( window.devicePixelRatio );
    laserView.renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( laserView.renderer.domElement );
    laserView.renderer.shadowMapEnabled = true;
    laserView.renderer.shadowMapSoft = true;
    laserView.renderer.shadowMapType = THREE.PCFSoftShadowMap;

    laserView.renderer.shadowCameraFar = laserView.camera.far;
    laserView.renderer.shadowCameraFov = 50;

    laserView.renderer.shadowMapBias = 0.0039;
    laserView.renderer.shadowMapDarkness = 0.5;
    laserView.renderer.shadowMapWidth = 1024;
    laserView.renderer.shadowMapHeight = 1024;
    laserView.renderer.render(laserView.scene, laserView.camera);

    //var orbit = new THREE.OrbitControls( camera, renderer.domElement );
    laserView.orbit.enableZoom = true;

    lights = [];
    lights[ 0 ] = new THREE.DirectionalLight( 0xffffff, 1 );
    lights[ 0 ].castShadow = true;
    lights[ 1 ] = new THREE.PointLight( 0xffffff, 0.4, 0 );
    lights[ 1 ].decay = 2;

    lights[ 0 ].position.set( 0, 0, 1000 );
    lights[ 1 ].position.set( 0, 0, 1000 );

    laserView.scene.add( lights[ 0 ] );
    laserView.scene.add( lights[ 1 ] );

    sphereMaterial = new THREE.MeshPhongMaterial( {
        transparent: false, 
        opacity: 1
     } );

    sphere = new THREE.Mesh(new THREE.SphereGeometry( 100, 32, 32 ), sphereMaterial);
    sphere.position.set(0,0,500);
    sphere.castShadow = true;
    //scene.add(sphere);

    window.addEventListener( 'resize', onWindowResize, false );

} // end init

function onWindowResize() {
    laserView.camera.aspect = window.innerWidth / window.innerHeight;
    laserView.camera.updateProjectionMatrix();
    laserView.renderer.setSize( window.innerWidth, window.innerHeight );
}

function loop() {
    update();
    animationSettings.time += animationSettings.timeStep;
    requestAnimationFrame(loop);
}

function sketch()
{
    laserView.orbit.controls.reset();
}

function update() {

    if (followMouse === true) {
        var mouse = getMousePosition();
        
        var vector = new THREE.Vector3(
            ( mouse.x / window.innerWidth ) * 2 - 1,
            -( mouse.y / window.innerHeight ) * 2 + 1,
            0.5 );
        vector.unproject( laserView.camera );
        var dir = vector.sub( laserView.camera.position ).normalize();
        var distance = - laserView.camera.position.z / dir.z;
        var pos = laserView.camera.position.clone().add( dir.multiplyScalar( distance ) );

        lights[1].position.set(pos.x, pos.y, 1000);
        sphere.position.set(pos.x, pos.y, 500);
    }

    laserView.renderer.render( laserView.scene, laserView.camera );
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
var followMouse = true;

function initGUI() {
    window.onload = function(){
    var gui = new dat.GUI();

    var directionalLight = lights[0];
    var directionalParams = {
        r: 1,
        g: 1,
        b: 1,
        intensity: 0.5
    };
    var directionalFolder = gui.addFolder('directional light');
    directionalFolder.add(directionalParams, 'r', 0, 1).name('red').onChange( function( value ) { directionalLight.color[0] = value; } );
    directionalFolder.add(directionalParams, 'g', 0, 1).name('green').onChange( function( value ) { directionalLight.color[1] = value; } );
    directionalFolder.add(directionalParams, 'b', 0, 1).name('blue').onChange( function( value ) { directionalLight.color[2] = value; } );
    directionalFolder.add(directionalParams, 'intensity', 0, 1).name('intensity').onChange( function( value ) { directionalLight.intensity = value; } );;


    var pointLight = lights[1];
    var pointParams = {
        r: 1,
        g: 1,
        b: 1,
        intensity: 0.5,
        z: 1500
    };
    var pointFolder = gui.addFolder('point light');
    pointFolder.add(pointParams, 'r', 0, 1).name('red').onChange( function( value ) { pointLight.color[0] = value; } );
    pointFolder.add(pointParams, 'g', 0, 1).name('green').onChange( function( value ) { pointLight.color[1] = value; } );
    pointFolder.add(pointParams, 'b', 0, 1).name('blue').onChange( function( value ) { pointLight.color[2] = value; } );
    pointFolder.add(pointParams, 'intensity', 0, 1).name('intensity').onChange( function( value ) { pointLight.intensity = value; } );
    pointFolder.add(pointParams, 'z', 0, 1500).name('distance').onChange( function( value ) { pointLight.position[2] = value; } );

    gui.add(window, 'followMouse').name('follow mouse');

    gui.add(window, 'sketch').name('sketch');
    }
}

// get mouse position within the canvas
getMousePosition = function() {
    var mouseX,
        mouseY,
        rect = laserView.renderCanvas.getBoundingClientRect();

    laserView.renderCanvas.addEventListener('mousemove', function(e) {
        mouseX = event.clientX - rect.left;
        mouseY = event.clientY - rect.top;
    });

    return function() {
        return {x:mouseX, y:mouseY};
    };
}();

initCamera();
initGUI();
requestAnimationFrame(loop);

