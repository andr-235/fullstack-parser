'use client'

import { useState } from 'react'
import { useComments } from '@/hooks/use-comments'
import { Search, ChevronDown, ExternalLink } from 'lucide-react'
import { VKCommentResponse } from '@/types/api'

export default function CommentsPage() {
  const { data, isLoading, error } = useComments()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterGroup, setFilterGroup] = useState('all')
  const [filterKeyword, setFilterKeyword] = useState('all')

  // TODO: Add actual filtering logic
  const filteredComments = data?.items

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title mb-4">Фильтры</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="form-control">
              <label className="input input-bordered flex items-center gap-2">
                <input
                  type="text"
                  className="grow"
                  placeholder="Поиск по тексту"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Search size={16} />
              </label>
            </div>
            <select className="select select-bordered w-full">
              <option disabled selected>
                Фильтр по группе
              </option>
              <option>Все группы</option>
              {/* TODO: Populate with real groups */}
              <option>Group 1</option>
              <option>Group 2</option>
            </select>
            <select className="select select-bordered w-full">
              <option disabled selected>
                Фильтр по слову
              </option>
              <option>Все слова</option>
              {/* TODO: Populate with real keywords */}
              <option>Keyword 1</option>
              <option>Keyword 2</option>
            </select>
          </div>
        </div>
      </div>

      {/* Comments List */}
      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Найденные комментарии</h2>
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex justify-center p-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : error ? (
              <div role="alert" className="alert alert-error">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="stroke-current shrink-0 h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span>Ошибка: {error.message}</span>
              </div>
            ) : (
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>Автор</th>
                    <th>Текст комментария</th>
                    <th>Группа</th>
                    <th>Дата</th>
                    <th>Ссылка</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredComments?.map((comment: VKCommentResponse) => (
                    <tr key={comment.id}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="avatar placeholder">
                            <div className="bg-neutral-focus text-neutral-content rounded-full w-12">
                              <span>
                                {comment.author_name?.substring(0, 1) || 'A'}
                              </span>
                            </div>
                          </div>
                          <div>
                            <div className="font-bold">
                              {comment.author_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="max-w-md">
                        <p className="truncate">{comment.text}</p>
                      </td>
                      <td>(Group)</td>
                      <td>
                        {new Date(comment.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <a
                          href={`https://vk.com/comment${comment.vk_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-ghost btn-xs"
                        >
                          <ExternalLink size={16} />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
