var galleryUploader = new qq.FineUploader({
    element: document.getElementById("fine-uploader-gallery"),
    template: 'qq-template-gallery',
    request: {
        endpoint: '../server/uploads/php.php'
    },
    thumbnails: {
        placeholders: {
            waitingPath: '../img/symbols/waiting-generic.png',
            notAvailablePath: '../img/symbols/not_available-generic.png'
        }
    },
    validation: {
        allowedExtensions: ['pdf', 'svg']
    }
});