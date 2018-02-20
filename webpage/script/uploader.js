var galleryUploader = new qq.FineUploader({
    element: document.getElementById("fine-uploader-gallery"),
    debug: true,
    template: 'qq-template-gallery',
    request: {
        endpoint: '../server/uploads/'
    },
    thumbnails: {
        placeholders: {
            waitingPath: '../img/symbols/waiting-generic.png',
            notAvailablePath: '../img/symbols/not_available-generic.png'
        }
    },
    validation: {
        allowedExtensions: ['pdf', 'svg', 'ai', 'png', 'jpg']
    }
});