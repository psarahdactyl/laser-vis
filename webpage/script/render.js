// canvas settings
var renderCanvas = document.getElementById("renderCanvas"),
    drawingCanvas = document.getElementById("drawingCanvas"),
    viewWidth = renderCanvas.clientWidth,
    viewHeight = renderCanvas.clientHeight,
    ctx,
    timeStep = (1/60),
    time = 0;


function initCamera() {
	isSketching = true;
    isExploded = false;
    drawingCanvas.style.visibility='visible';

    camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 100, 10000 );
    camera.position.set( 0, 0, 1000 );
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xffffff );

    // instantiate a loader
    var loader = new THREE.TextureLoader();

    var width,height;

    // load a resource
    var texture = loader.load(
        // resource URL
        /*drawingCanvas.dataURL()*/
        "../img/Birch-Plywood.jpg", function () {
            width = texture.image.width;
            height = texture.image.height;
            plane.scale.x = width;
            plane.scale.y = height;
        });

    var normal = loader.load("../img/_normal.png");
    var displacement = loader.load("../img/_displacement.png");
        
    var material = new THREE.MeshPhongMaterial( {
        map: texture,
        normalMap: normal,
        displacementMap: displacement,
        displacementScale: 10,
        displacementBias: -0.5,
        //alphaMap: alpha_even,
        specular: 15
     } );
    material.alphaTest = 0.5;

    plane = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1, 350, 350, 1), material);
    plane.material.needsUpdate = true; // update material
    plane.receiveShadow = true;
    
    plane.name = "onePlane";

    scene.add( plane );
        
    renderer = new THREE.WebGLRenderer( { canvas:renderCanvas } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight * 0.85 );
    document.body.appendChild( renderer.domElement );
    renderer.shadowMapEnabled = true;
    renderer.shadowMapSoft = true;
    renderer.shadowMapType = THREE.PCFSoftShadowMap;

    renderer.shadowCameraFar = camera.far;
    renderer.shadowCameraFov = 50;

    renderer.shadowMapBias = 0.0039;
    renderer.shadowMapDarkness = 0.5;
    renderer.shadowMapWidth = 1024;
    renderer.shadowMapHeight = 1024;
    renderer.render(scene, camera);

    orbit = new THREE.OrbitControls( camera, renderer.domElement );
    //orbit.enableZoom = true;

    lights = [];
    lights[ 0 ] = new THREE.DirectionalLight( 0xffffff, 1 );
    lights[ 0 ].castShadow = true;
    lights[ 1 ] = new THREE.PointLight( 0xffffff, 0.4, 0 );
    lights[ 1 ].decay = 2;
    //lights[ 1 ].castShadow = true;

    lights[ 0 ].position.set( 0, 0, 1000 );
    lights[ 1 ].position.set( 0, 0, 1000 );

    scene.add( lights[ 0 ] );
    scene.add( lights[ 1 ] );

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

//document.getElementById("explodeButton").addEventListener ("click", explodeView, false);
//document.getElementById("designButton").addEventListener ("click", sketch, false);

function explodeView() {
    var plane_even, plane_odd;

    if(!isExploded) {
        plane.visible = false;

        // instantiate a loader
        var loader = new THREE.TextureLoader();

        // load a resource
        var texture = loader.load(
        // resource URL
        /*drawingCanvas.dataURL()*/
        "../img/Birch-Plywood.jpg", function () {
            width = texture.image.width;
            height = texture.image.height;
            plane_odd.scale.x = width;
            plane_odd.scale.y = height;
            plane_even.scale.x = width;
            plane_even.scale.y = height;
            plane_odd.position.set(width/2,0,height/4);
            plane_odd.name = "oddPlane";
            plane_even.name = "evenPlane";
        });

        // var normal = loader.load("../img/a_cut.png_normal.png");
        // var displacement = loader.load("../img/a_cut.png_displacement.png");
        var normal = loader.load("../img/_normal.png");
        var displacement = loader.load("../img/_displacement.png");
        var alpha_odd = loader.load("../img/odd_components.png");
        var alpha_even = loader.load("../img/even_components.png");
            
        var material_even = new THREE.MeshPhongMaterial( {
            map: texture,
            normalMap: normal,
            displacementMap: displacement,
            displacementScale: 10,
            displacementBias: -0.5,
            alphaMap: alpha_even,
            specular: 15
         } );
        material_even.alphaTest = 0.5;

        var material_odd = new THREE.MeshPhongMaterial( {
            map: texture,
            normalMap: normal,
            displacementMap: displacement,
            displacementScale: 10,
            displacementBias: -0.5,
            alphaMap: alpha_odd,
            specular: 15
         } );
        material_odd.alphaTest = 0.5;

        plane_even = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1, 10, 10, 1), material_even);
        plane_even.material.needsUpdate = true; // update material
        
        scene.add( plane_even );
        plane_even.position.set(0,0,0);

        plane_odd = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1, 300, 300, 1), material_odd);
        plane_odd.material.needsUpdate = true; // update material
        
        scene.add( plane_odd );
        
        //plane_odd.position.set(1000,0,0);
    } else {
        plane_odd = scene.getObjectByName("oddPlane", true);
        plane_even = scene.getObjectByName("evenPlane", true);
        scene.remove(plane_odd);
        scene.remove(plane_even);
        plane.visible = true;
    }
    console.log('explode');
    console.log(isExploded);
    isExploded = !isExploded;

}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight * 0.85;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight * 0.85 );
}

function loop() {
    update();
    time += timeStep;
    requestAnimationFrame(loop);
}

document.addEventListener("keydown", onDocumentKeyDown, false);
function onDocumentKeyDown(event) {
    var keyCode = event.which;
    if (keyCode == 32) {
    	sketch();
    }
};

function swapCanvases() {
	if (drawingCanvas.style.visibility=='visible') {
		drawingCanvas.style.visibility='hidden';
		renderCanvas.style.visibility='visible';
	} else {
		drawingCanvas.style.visibility='visible';
		//renderCanvas.style.visibility='hidden';
	}
}

function sketch() {
    isSketching = !isSketching;

	if (isSketching) {
	    orbit.reset();
	    orbit.minPolarAngle = Math.PI/2;
		orbit.maxPolarAngle = Math.PI/2;
		orbit.minAzimuthAngle = 0;
		orbit.maxAzimuthAngle = 0;
	} else {
        orbit.reset();
		orbit.minPolarAngle = 0;
		orbit.maxPolarAngle = Math.PI;
		orbit.minAzimuthAngle = - Infinity;
		orbit.maxAzimuthAngle = Infinity;
	}
    console.log('sketch mode');
    console.log(isSketching);
	swapCanvases();
}

function update() {

    if (followMouse === true) {
        var mouse = getMousePosition();
        
        var vector = new THREE.Vector3(
            ( mouse.x / window.innerWidth ) * 2 - 1,
            -( mouse.y / window.innerHeight ) * 2 + 1,
            0.5 );
        vector.unproject( camera );
        var dir = vector.sub( camera.position ).normalize();
        var distance = - camera.position.z / dir.z;
        var pos = camera.position.clone().add( dir.multiplyScalar( distance ) );

        lights[1].position.set(pos.x, pos.y, 1000);
        sphere.position.set(pos.x, pos.y, 500);
    }

    renderer.render( scene, camera );
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
        rect = renderCanvas.getBoundingClientRect();

    renderCanvas.addEventListener('mousemove', function(e) {
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
