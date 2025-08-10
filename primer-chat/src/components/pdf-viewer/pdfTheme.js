const urlParams = new URLSearchParams(window.location.search)
const theme = urlParams.get('theme') || 'light'

document.documentElement.setAttribute('data-theme', theme)
