const api = require('../../utils/api.js');

Page({
  data: {
    selectedImage: '',
    customText: '西施',
    languages: ['中文', '英文', '日文', '韩文', '德文', '法文', '西班牙文', '俄文'],
    languageIndex: 0,
    colorMode: true,
    portraitMode: false,
    loading: false
  },

  chooseImage() {
    tt.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFiles && res.tempFiles[0] && res.tempFiles[0].tempFilePath
          || res.tempFilePaths && res.tempFilePaths[0];
        if (tempFilePath) {
          this.setData({ selectedImage: tempFilePath });
        }
      },
      fail: (err) => {
        console.error('chooseMedia fail:', JSON.stringify(err));
        tt.showToast({
          title: '选择图片失败',
          icon: 'none',
          duration: 3000
        });
      }
    });
  },

  onCustomTextChange(e) {
    this.setData({ customText: e.detail.value });
  },

  onLanguageChange(e) {
    this.setData({ languageIndex: parseInt(e.detail.value) });
  },

  onColorModeChange(e) {
    this.setData({ colorMode: e.detail.value });
  },

  onPortraitModeChange(e) {
    this.setData({ portraitMode: e.detail.value });
  },

  generateArt() {
    if (!this.data.selectedImage || this.data.loading) {
      return;
    }

    const languageMap = ['chinese', 'english', 'japanese', 'korean', 'german', 'french', 'spanish', 'russian'];

    this.setData({ loading: true });

    tt.showLoading({
      title: '生成中...',
      mask: true
    });

    api.generateAsciiArt(this.data.selectedImage, {
      customText: this.data.customText,
      language: languageMap[this.data.languageIndex],
      color: this.data.colorMode,
      portrait: this.data.portraitMode
    }).then((result) => {
      console.log('生成成功，result:', JSON.stringify(result));
      
      if (!result || !result.image_url) {
        throw new Error('响应格式错误：' + JSON.stringify(result));
      }
      
      var imageUrl = result.image_url;
      if (imageUrl && imageUrl.indexOf('http') !== 0) {
        imageUrl = 'https://weixin.52iptv.net' + imageUrl;
      }
      console.log('完整图片 URL:', imageUrl);

      tt.hideLoading();
      this.setData({ loading: false });

      tt.navigateTo({
        url: '/pages/result/result?imageUrl=' + encodeURIComponent(imageUrl),
        success: () => {
          console.log('navigateTo 成功');
        },
        fail: (navErr) => {
          console.error('navigateTo 失败:', JSON.stringify(navErr));
          tt.showToast({ title: '页面跳转失败', icon: 'none' });
        }
      });
    }).catch((err) => {
      tt.hideLoading();
      this.setData({ loading: false });
      var errMsg = err.message || err.errMsg || JSON.stringify(err);
      tt.showToast({
        title: '生成失败：' + errMsg,
        icon: 'none',
        duration: 5000
      });
      console.error('Generate error:', err);
    });
  }
});
