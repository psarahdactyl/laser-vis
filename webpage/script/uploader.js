var uploader = new qq.FineUploader({
    element: document.getElementById("uploader"),
    validation: {
        allowedExtensions: ['pdf', 'svg', 'ai', 'png', 'jpg']
    },
    extraButtons: [
        {
            element: document.getElementById("uploadButton"),
            validation: {
                allowedExtensions: ['pdf', 'svg', 'ai', 'png', 'jpg']
            }
        }
    ]
});