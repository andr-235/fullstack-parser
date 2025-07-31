import '@testing-library/jest-dom'

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R
      toHaveClass(className: string): R
      toHaveAttribute(attr: string, value?: string): R
      toHaveTextContent(text: string): R
      toBeVisible(): R
      toBeDisabled(): R
      toBeEnabled(): R
      toBeChecked(): R
      toBePartiallyChecked(): R
      toHaveValue(value: string | string[] | number): R
      toHaveDisplayValue(value: string | string[]): R
      toBeRequired(): R
      toBeInvalid(): R
      toBeValid(): R
      toHaveAccessibleName(name: string): R
      toHaveAccessibleDescription(description: string): R
      toHaveStyle(css: string | Record<string, any>): R
      toHaveFocus(): R
      toHaveFormValues(expectedValues: Record<string, any>): R
      toBeEmptyDOMElement(): R
      toHaveErrorMessage(text: string | RegExp): R
    }
  }
}
