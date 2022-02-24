import ListIssues from './ListIssues.vue'
import mountComponent from './mountComponent'

const props = {
  rawBounds: rawData.bounds, // eslint-disable-line no-undef
  rawIssues: rawData.issues, // eslint-disable-line no-undef
  rawFilters: rawData.filters, // eslint-disable-line no-undef
  allTags: rawData.allTags // eslint-disable-line no-undef
}
mountComponent(ListIssues, props, '#list-issues-map')
