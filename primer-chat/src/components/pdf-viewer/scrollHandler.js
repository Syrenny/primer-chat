// scrollHandler.js
(() => {
    const HIGHLIGHT_LAYER_CLASS = 'pc-highlight-layer'
    const HIGHLIGHT_BOX_CLASS = 'pc-highlight-box'

    const state = {
        positions: null, // последняя подсветка
        busBound: false,
    }

    function ensureHighlightLayer(pageView) {
        const wrapper = pageView.div.querySelector('.canvasWrapper')
        let layer = wrapper && wrapper.querySelector('.pc-highlight-layer')
        if (!layer && wrapper) {
            layer = document.createElement('div')
            layer.className = 'pc-highlight-layer'
            Object.assign(layer.style, {
                position: 'absolute',
                inset: '0',
                pointerEvents: 'none',
                // ВАЖНО: ниже textLayer (z=2) и annotationLayer (z=3)
                zIndex: '10', // ниже textLayer (2) и annotationLayer (3)
            })
            wrapper.appendChild(layer)
        }
        return layer
    }


    function clearHighlights() {
        document.querySelectorAll(`.${HIGHLIGHT_LAYER_CLASS}`).forEach((n) => n.remove())
    }

    function renderPositions(positions) {
        clearHighlights()
        if (!positions?.length) return

        for (const pos of positions) {
            const pageIndex = pos.page - 1
            const pageView = PDFViewerApplication.pdfViewer.getPageView(pageIndex)
            if (!pageView || !pageView.pdfPage) continue

            // ВАЖНО: используем уже готовый viewport страницы
            const viewport = pageView.viewport // корректный с учётом scale/rotation/CSS_UNITS

            // pos.xyxy ДОЛЖЕН быть в PDF-координатах (bottom-left, pt)
            const [x1, y1, x2, y2] = pos.xyxy
            const [vx1, vy1, vx2, vy2] = viewport.convertToViewportRectangle([x1, y1, x2, y2])

            const left = Math.min(vx1, vx2)
            const top = Math.min(vy1, vy2)
            const width = Math.abs(vx2 - vx1)
            const height = Math.abs(vy2 - vy1)

            const layer = ensureHighlightLayer(pageView)
            if (!layer) continue

            // лёгкая «толстая» подсветка
            const box = document.createElement('div')
            box.className = HIGHLIGHT_BOX_CLASS
            Object.assign(box.style, {
                position: 'absolute',
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
                background: 'rgba(255, 221, 87, 0.28)',
                boxShadow: 'inset 0 0 0 1px rgba(255,170,0,0.8)',
                borderRadius: '2px',
            })

            layer.appendChild(box)

            // Диагностика (разово на первую позицию)
            if (pos === positions[0]) {
                // сверим ещё высоту страницы — частая причина «константного сдвига»
                const debugViewport1 = pageView.pdfPage.getViewport({ scale: 1, rotation: 0 })
                console.debug('[pc] p=', pos.page, {
                    pdf_bbox: pos.xyxy,
                    viewport_used: { width: viewport.width, height: viewport.height, scale: viewport.scale, rotation: viewport.rotation },
                    page_height_pt_pdfjs: debugViewport1.height,
                    rect_css: { left, top, width, height }
                })
            }
        }
    }

    function scrollToFirst(positions) {
        const first = positions[0]
        const pageView = PDFViewerApplication.pdfViewer.getPageView(first.page - 1)
        if (!pageView || !pageView.pdfPage) return

        const viewport = pageView.viewport
        const [x1, y1, x2, y2] = viewport.convertToViewportRectangle(first.xyxy)
        const y = Math.min(y1, y2)
        const container = PDFViewerApplication.pdfViewer.container
        const top = pageView.div.offsetTop + y - 60
        container.scrollTo({ top, behavior: 'smooth' })
    }

    function bindEventBusOnce() {
        if (state.busBound) return
        const bind = () => {
            const bus = PDFViewerApplication?.eventBus
            if (!bus) return

            const reRender = () => state.positions && renderPositions(state.positions)
            bus.on('scalechanging', reRender)
            bus.on('rotationchanging', reRender)
            bus.on('pagerendered', reRender)
            bus.on('documentloaded', () => {
                state.positions = null
                clearHighlights()
            })

            state.busBound = true
        }
        PDFViewerApplication?.initializedPromise ? PDFViewerApplication.initializedPromise.then(bind) : bind()
    }

    window.addEventListener('message', (event) => {
        const data = event.data
        if (!data) return

        // Поддержим оба формата: старый (pageNumber + bbox) и новый (positions[])
        let positions = null

        if (data.type === 'highlight-chunk') {
            positions = data.payload?.positions ?? null
        } else if (data.type === 'scroll-to-chunk') {
            const { pageNumber, bbox } = data.payload || {}
            if (pageNumber && bbox) {
                positions = [{ page: pageNumber, xyxy: bbox }]
            }
        } else {
            return
        }

        if (!positions || !positions.length) return

        bindEventBusOnce()

        // Убедимся, что документ и viewer готовы
        const run = () => {
            renderPositions(positions)
            scrollToFirst(positions)
            state.positions = positions
        }

        if (PDFViewerApplication?.initializedPromise) {
            PDFViewerApplication.initializedPromise.then(run)
        } else {
            run()
        }
    })
})()
