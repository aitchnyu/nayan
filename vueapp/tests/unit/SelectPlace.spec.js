import axios from 'axios'
import { mount } from '@vue/test-utils'
import SelectPlace from '../../src/SelectPlace'

jest.mock('axios')

describe('SelectPlace.vue', () => {
  it('Can search stuff', async () => {
    const wrapper = mount(SelectPlace, {
      propsData: { center: { lat: 60, lng: 60 }, onSelect: () => 1 }
    })
    await wrapper.vm.rawFetch('')
    axios.get.mockResolvedValue({
      data: {
        points: [
          { id: 2, name: 'foo', point: { lat: 61, lng: 61 } },
          { id: 2, name: 'foo 2', point: { lat: 61, lng: 61 } }]
      }
    })
    await wrapper.vm.rawFetch('f')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.data).toEqual([
      { id: 2, name: 'foo', point: { lat: 61, lng: 61 } },
      { id: 2, name: 'foo 2', point: { lat: 61, lng: 61 } }])
  })
})
