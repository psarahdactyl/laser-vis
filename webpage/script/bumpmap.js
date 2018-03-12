 var canvas = document.getElementById('mainCanvas');
    var ctx = canvas.getContext("2d");
    var date = new Date();
    var pn = new Perlin('rnd' + date.getTime());
    fillWithPerlin(pn, ctx);
    function fillWithPerlin(perlin, ctx) {
        for (var x = 0; x < 512; x++) {
            for (var y = 0; y < 512; y++) {
                var base = new THREE.Color(0xffffff);
                var value = perlin.noise(x / 10, y / 10, 0);
                base.multiplyScalar(value);
                ctx.fillStyle = "#" + base.getHexString();
                ctx.fillRect(x, y, 1, 1);
            }
        }
    }
   function init() {
        var gui = new dat.GUI();
        gui.add(controls, "regenerateMap");
        gui.add(controls, "bumpScale", -2, 2).onChange(controls.updateScale);
        render();
        function createMesh(geom, texture) {
            var texture = THREE.ImageUtils.loadTexture("../assets/textures/general/" + texture);
            var bumpMap = new THREE.Texture(canvas);
            geom.computeVertexNormals();
            var mat = new THREE.MeshPhongMaterial();
            mat.color = new THREE.Color(0x77ff77);
            mat.bumpMap = bumpMap;
            bumpMap.needsUpdate = true;
            // create a multimaterial
            var mesh = new THREE.Mesh(geom, mat);
            return mesh;
        }
        function render() {
            stats.update();
            cube.rotation.y += 0.01;
            cube.rotation.x += 0.01;
            // render using requestAnimationFrame
            requestAnimationFrame(render);
            webGLRenderer.render(scene, camera);
        }

    }
    window.onload = init;