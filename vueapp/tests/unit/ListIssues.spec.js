import { mount } from '@vue/test-utils'
import ListIssues from '@/ListIssues.vue'

describe('ListIssues.vue', () => {
  it('can list issues', async () => {
    window.getMapDimensions = () => ({ width: 4000, height: 3000 })
    const wrapper = mount(ListIssues, {
      propsData: {
        rawBounds: [
          { lat: 10, lng: 77 },
          { lat: 10, lng: 75 },
          { lat: 9, lng: 75 },
          { lat: 9, lng: 77 }
        ],
        rawIssues: [
          {
            id: 1,
            title: 'foo',
            location: { lat: 60.1, lng: 60.2 }
          },
          {
            id: 2,
            title: 'foo 2',
            location: { lat: 60.3, lng: 60.3 }
          }]
      }
    })
    expect(wrapper.vm.width).toBe(4000)
    expect(wrapper.vm.height).toBe(3000)
    window.getMapDimensions = () => ({ width: 5000, height: 4000 })
    wrapper.vm.onResize()
    expect(wrapper.vm.width).toBe(5000)
    expect(wrapper.vm.height).toBe(4000)
    await wrapper.vm.$nextTick()
    // Since the map has corners same as each other, it has a distance of 0
    expect(wrapper.vm.recenterUrl).toBe('/issues/9.500365096717932/75.99999999999999/0')
  })
})
