declare module 'react-window-infinite-loader' {
  import { ReactNode } from 'react'

  interface InfiniteLoaderProps {
    isItemLoaded: (index: number) => boolean
    itemCount: number
    loadMoreItems: (startIndex: number, stopIndex: number) => Promise<void>
    children: (props: {
      onItemsRendered: (props: {
        visibleStartIndex: number
        visibleStopIndex: number
      }) => void
      ref: React.RefObject<any>
    }) => ReactNode
  }

  export default function InfiniteLoader(
    props: InfiniteLoaderProps
  ): JSX.Element
}
