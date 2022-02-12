// https://stackoverflow.com/questions/54382414/fixing-react-leaflet-testing-error-cannot-read-property-layeradd-of-null
// This allows Leaflet to render polygons for tests

var createElementNSOrig = global.document.createElementNS
global.document.createElementNS = function (namespaceURI, qualifiedName) {
  if (namespaceURI === 'http://www.w3.org/2000/svg' && qualifiedName === 'svg') {
    var element = createElementNSOrig.apply(this, arguments)
    element.createSVGRect = function () {}
    return element
  }
  return createElementNSOrig.apply(this, arguments)
}
