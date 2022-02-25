import Vue from 'vue'

Vue.config.productionTip = false

// https://github.com/webpack/webpack/issues/7077#issuecomment-383029585
const url = new URL(document.currentScript.src)
// eslint-disable-next-line no-undef, camelcase
__webpack_public_path__ = (url.origin + __webpack_public_path__)

export default function (component, selector) {
  const elem = document.getElementById(selector)
  return new Vue({
    render: h => h(component, { props: JSON.parse(elem.dataset.props) })
  }).$mount(elem)
}
