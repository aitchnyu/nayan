import { mount } from '@vue/test-utils'
import ViewIssue from '@/ViewIssue.vue'

describe('ViewIssue.vue', () => {
  it('renders Leaflet map centered at 60, 60', () => {
    const wrapper = mount(ViewIssue, {
      propsData: { title: 'foo', lat: 60, lng: 60 }
    })
    expect(wrapper.vm.leafletCenter()).toEqual({ lat: 60, lng: 60 })
  })
})
