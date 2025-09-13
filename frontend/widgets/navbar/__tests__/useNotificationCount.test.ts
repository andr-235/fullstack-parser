import { renderHook, waitFor } from '@testing-library/react'

import { useNotificationCount } from '../useNotificationCount'

describe('useNotificationCount', () => {

  it('возвращает число', () => {
    const { result } = renderHook(() => useNotificationCount())

    expect(typeof result.current).toBe('number')
  })
})
