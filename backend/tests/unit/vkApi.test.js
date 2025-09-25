process.env.VK_TOKEN = 'test-token';

const mockAxiosInstance = {
  get: jest.fn(),
  interceptors: {
    request: { use: jest.fn() },
    response: { use: jest.fn() }
  }
};

const mockAxios = {
  create: jest.fn(() => mockAxiosInstance)
};

jest.mock('axios', () => mockAxios);

const retryFn = jest.fn();
retryFn.exponentialDelay = jest.fn((attempt) => attempt * 100);

jest.mock('axios-retry', () => {
  const patch = (...args) => retryFn(...args);
  patch.exponentialDelay = retryFn.exponentialDelay;
  patch.default = patch;
  return patch;
});

const vkApi = require('../../src/repositories/vkApi');

describe('VKApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAxiosInstance.get.mockReset();
    mockAxios.create.mockImplementation(() => mockAxiosInstance);
  });

  describe('getPosts', () => {
    it('возвращает объект с постами', async () => {
      const mockResponse = {
        response: {
          items: [
            { id: 1, text: 'Post 1', date: 170, likes: { count: 5 } },
            { id: 2, text: 'Post 2', date: 180, likes: { count: 7 } }
          ]
        }
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await vkApi.getPosts(123);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('wall.get', {
        params: expect.objectContaining({ owner_id: -123, access_token: 'test-token', v: '5.199' })
      });
      expect(result).toEqual({
        posts: [
          expect.objectContaining({ id: 1, likes: 5 }),
          expect.objectContaining({ id: 2, likes: 7 })
        ]
      });
    });

    it('пробрасывает ошибки API', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('fail'));

      await expect(vkApi.getPosts(123)).rejects.toThrow('fail');
    });
  });

  describe('getComments', () => {
    it('агрегирует страницы комментариев', async () => {
      const firstPage = {
        response: {
          items: [{ id: 1, text: 'Comment 1', likes: { count: 1 } }]
        }
      };
      const secondPage = {
        response: {
          items: [{ id: 2, text: 'Comment 2', likes: { count: 2 } }]
        }
      };

      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: firstPage })
        .mockResolvedValueOnce({ data: secondPage });

      const result = await vkApi.getComments(123, 1);

      expect(mockAxiosInstance.get).toHaveBeenNthCalledWith(1, 'wall.getComments', expect.objectContaining({
        params: expect.objectContaining({ offset: 0 })
      }));
      expect(mockAxiosInstance.get).toHaveBeenNthCalledWith(2, 'wall.getComments', expect.objectContaining({
        params: expect.objectContaining({ offset: 100 })
      }));
      expect(result).toEqual({
        comments: expect.arrayContaining([
          expect.objectContaining({ id: 1, likes: 1 }),
          expect.objectContaining({ id: 2, likes: 2 })
        ])
      });
    });
  });
});