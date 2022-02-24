import { mount } from '@vue/test-utils'
import ListIssues from '../../src/ListIssues'

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
          }],
        rawFilters: {
          all: [],
          any: [],
          none: []
        },
        allTags: []
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
    // todo remove this
    expect(wrapper.vm.recenterUrl).toBe('/issues/9.500365096717932/75.99999999999999/0')
  })

  it('can filter', async () => {
    // window.getMapDimensions = () => ({ width: 4000, height: 3000 })
    // window.location = 'http://localhost:8000/issues/9.999353928446595/76.29239170629624/1396'
    const wrapper = mount(ListIssues, {
      propsData: {
        rawBounds: [
          { lat: 10, lng: 77 },
          { lat: 10, lng: 75 },
          { lat: 9, lng: 75 },
          { lat: 9, lng: 77 }
        ],
        rawIssues: [],
        rawFilters: {
          all: [],
          any: [],
          none: []
        },
        allTags: []
      }
    })
    wrapper.vm.updateTagFilters('all', [{ name: 'Foo 1', slug: 'foo-1' }, { name: 'Foo 2', slug: 'foo-2' }])
    // window.location is apparently blank
    expect(wrapper.vm.urlForUpdatedTagFilters).toBe('/?all_tags=foo-1%2Cfoo-2')
    wrapper.vm.updateTagFilters('none', [{ name: 'Foo 2', slug: 'foo-2' }])
    console.log('none filter ', wrapper.vm.urlForUpdatedTagFilters)
    expect(wrapper.vm.urlForUpdatedTagFilters).toBe('/?all_tags=foo-1&none_tags=foo-2')
    wrapper.vm.updateTagFilters('any', [{ name: 'Foo 2', slug: 'foo-2' }])
    expect(wrapper.vm.urlForUpdatedTagFilters).toBe('/?all_tags=foo-1&any_tags=foo-2')
  })
})
