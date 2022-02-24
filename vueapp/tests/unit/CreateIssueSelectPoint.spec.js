import { mount } from '@vue/test-utils'
import CreateIssueSelectPoint from '../../src/CreateIssueSelectPoint'

describe('CreateIssueSelectPoint.vue', () => {
  it('renders Leaflet map centered at 60, 60', async () => {
    const wrapper = mount(CreateIssueSelectPoint, {
      propsData: { center: { lat: 60, lng: 60 } }
    })
    expect(wrapper.vm.getLeafletCenter()).toEqual({ lat: 60, lng: 60 })
    expect(wrapper.find('input[name=latitude]').element.value).toEqual('60')
    expect(wrapper.find('input[name=longitude]').element.value).toEqual('60')
    wrapper.vm.setLeafletCenter(60.1, 60.2)
    expect(wrapper.vm.secondCenter).toEqual({ lat: 60.1, lng: 60.2 })
    await wrapper.vm.$nextTick() // Without this wait, values below won't be updated
    expect(wrapper.find('input[name=latitude]').element.value).toEqual('60.1')
    expect(wrapper.find('input[name=longitude]').element.value).toEqual('60.2')
  })
})
