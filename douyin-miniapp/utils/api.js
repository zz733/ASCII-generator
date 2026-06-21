const app = getApp();

const ENV_CONFIG = {
  development: 'https://weixin.52iptv.net/api',
  staging: 'https://weixin.52iptv.net/api',
  production: 'https://weixin.52iptv.net/api'
};

const ENV = 'production';
const API_BASE_URL = (app && app.globalData && app.globalData.apiBaseUrl) || ENV_CONFIG[ENV] || ENV_CONFIG.development;

function request(options) {
  return new Promise((resolve, reject) => {
    tt.request({
      url: options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(`Request failed: ${res.statusCode}`));
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
}

function uploadFile(options) {
  return new Promise((resolve, reject) => {
    tt.uploadFile({
      url: options.url,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          var data = res.data;
          if (typeof data === 'string') {
            try {
              data = JSON.parse(data);
            } catch (e) {
              reject(new Error('Response parse error'));
              return;
            }
          }
          resolve(data);
        } else {
          reject(new Error(`Upload failed: ${res.statusCode}`));
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
}

function generateAsciiArt(filePath, options = {}) {
  const formData = {
    custom_text: options.customText || '西施',
    language: options.language || 'chinese',
    color: options.color !== undefined ? String(options.color) : 'true',
    portrait: options.portrait !== undefined ? String(options.portrait) : 'false'
  };

  return uploadFile({
    url: `${API_BASE_URL}/generate/`,
    filePath: filePath,
    name: 'file',
    formData: formData
  });
}

module.exports = {
  request,
  uploadFile,
  generateAsciiArt,
  API_BASE_URL
};
