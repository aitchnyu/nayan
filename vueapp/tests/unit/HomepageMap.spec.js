// import jest from 'jest'
import { mount } from '@vue/test-utils'
import HomepageMap from '@/HomepageMap.vue'

jest.mock('axios', () => ({
  get: Promise.resolve('value')
}))

describe('HomepageMap.vue', () => {
  it('HomepageMap can access user location', async () => {
    const mock = jest.spyOn(HomepageMap.methods, 'getPosition')
      .mockImplementation(() => ({ coords: { latitude: 60, longitude: 60 } }))
    const wrapper = mount(HomepageMap, {
      propsData: {}
    })
    expect(mock).toBeCalled()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.userLocationMarker).toEqual({ lat: 60, lng: 60 })
    expect(wrapper.vm.getLeaflet().getCenter()).toEqual({ lat: 60, lng: 60 })
    wrapper.vm.selectPlace({ id: 1, name: 'foo', point: { lat: 61, lng: 61 } })
    expect(wrapper.vm.getLeaflet().getCenter()).toEqual({ lat: 61, lng: 61 })
    expect(wrapper.vm.selected).toEqual({ id: 1, name: 'foo', point: { lat: 61, lng: 61 } })
    wrapper.vm.selectPlace(null)
    expect(wrapper.vm.getLeaflet().getCenter()).toEqual({ lat: 61, lng: 61 })
    expect(wrapper.vm.selected).toEqual({ id: 1, name: 'foo', point: { lat: 61, lng: 61 } })
    wrapper.vm.selectPlace({ id: 2, name: 'foo 2', point: { lat: 62, lng: 62 } })
    expect(wrapper.vm.getLeaflet().getCenter()).toEqual({ lat: 62, lng: 62 })
    expect(wrapper.vm.selected).toEqual({ id: 2, name: 'foo 2', point: { lat: 62, lng: 62 } })
  })
  it('HomepageMap has an error accessing location', async () => {
    const mock = jest.spyOn(HomepageMap.methods, 'getPosition')
      // eslint-disable-next-line no-throw-literal
      .mockImplementation(() => { throw { message: 'fake message' } })
    const wrapper = mount(HomepageMap, {
      propsData: {}
    })
    expect(mock).toBeCalled()
    expect(wrapper.vm.locationErrorMessage).toBe('fake message')
  })
})
