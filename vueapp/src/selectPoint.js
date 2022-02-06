import SelectPoint from './SelectPoint'
import mountComponent from './mountComponent'

// eslint-disable-next-line no-undef
const props = { initialLatitude: rawData.latitude, initialLongitude: rawData.longitude }
mountComponent(SelectPoint, props, '#select-point')
