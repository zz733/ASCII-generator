Page({
  data: {
    resultImage: '',
    localImagePath: ''
  },

  onLoad(options) {
    console.log('result onLoad options:', JSON.stringify(options));
    if (options.imageUrl) {
      var imageUrl = decodeURIComponent(options.imageUrl);
      console.log('远程图片URL:', imageUrl);
      this.setData({ resultImage: imageUrl });
    }
  },

  onImageLoad(e) {
    console.log('图片加载成功:', e.detail);
  },

  onImageError(e) {
    console.error('图片加载失败:', JSON.stringify(e.detail));
  },

  previewImage() {
    if (this.data.resultImage) {
      tt.previewImage({
        urls: [this.data.resultImage],
        current: this.data.resultImage
      });
    }
  },

  saveImage() {
    if (!this.data.resultImage) {
      return;
    }

    if (this.data.localImagePath) {
      this.doSave(this.data.localImagePath);
      return;
    }

    tt.showLoading({ title: '准备保存...' });
    tt.downloadFile({
      url: this.data.resultImage,
      success: (res) => {
        tt.hideLoading();
        if (res.statusCode === 200 && res.tempFilePath) {
          this.setData({ localImagePath: res.tempFilePath });
          this.doSave(res.tempFilePath);
        } else {
          tt.showToast({ title: '下载失败', icon: 'none' });
        }
      },
      fail: (err) => {
        tt.hideLoading();
        console.error('downloadFile fail:', JSON.stringify(err));
        tt.showToast({ title: '下载失败', icon: 'none' });
      }
    });
  },

  doSave(filePath) {
    tt.saveImageToPhotosAlbum({
      filePath: filePath,
      success: () => {
        tt.showToast({ title: '保存成功', icon: 'success' });
      },
      fail: (err) => {
        console.error('saveImage fail:', JSON.stringify(err));
        if (err.errMsg && (err.errMsg.indexOf('auth deny') !== -1 || err.errMsg.indexOf('authorize') !== -1)) {
          tt.showModal({
            title: '提示',
            content: '需要您授权保存图片到相册',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                tt.openSetting();
              }
            }
          });
        } else {
          tt.showToast({ title: '保存失败', icon: 'none' });
        }
      }
    });
  },

  onShareAppMessage() {
    return {
      title: '看看我的 ASCII 艺术！',
      path: '/pages/index/index'
    };
  },

  goBack() {
    tt.navigateBack();
  }
});
