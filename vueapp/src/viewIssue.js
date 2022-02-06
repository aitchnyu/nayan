import ViewIssue from './ViewIssue'
import mountComponent from './mountComponent'

// eslint-disable-next-line no-undef
const props = { lat: rawData.lat, lng: rawData.lng }
mountComponent(ViewIssue, props, '#issue-map')
