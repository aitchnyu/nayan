import ListIssues from './ListIssues.vue'
import mountComponent from './mountComponent'

// eslint-disable-next-line no-undef
const props = { rawBounds: rawData.bounds, rawIssues: rawData.issues }
mountComponent(ListIssues, props, '#list-issues-map')
