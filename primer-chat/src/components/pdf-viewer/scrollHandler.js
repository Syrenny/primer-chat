window.addEventListener('message', event => {
    if (!event.data || event.data.type !== 'scroll-to-chunk') return

    const { pageNumber, bbox } = event.data.payload

    const [x1, y1, x2, y2] = bbox

    // Получаем страницу
    const pageView = PDFViewerApplication.pdfViewer.getPageView(pageNumber - 1)
    if (!pageView) return

    pageView.pdfPage.getViewport({ scale: pageView.scale }).then(viewport => {
        const [vx1, vy1, vx2, vy2] = viewport.convertToViewportRectangle(bbox)

        // Скроллим до центра bbox (или его верхней границы)
        const scrollContainer = PDFViewerApplication.pdfViewer.container
        const pageDiv = pageView.div

        const rectTop = pageDiv.offsetTop + Math.min(vy1, vy2)
        scrollContainer.scrollTo({
            top: rectTop - 50, // небольшой отступ
            behavior: 'smooth'
        })
    })
})
