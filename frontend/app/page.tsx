import { redirect } from 'next/navigation'

export default function MainRoute() {
  // Перенаправляем на dashboard как основную страницу
  redirect('/dashboard')
}
