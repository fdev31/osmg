const getAvatarComponent = (svgData) => {
	return {
		created() {
			this.domId = 'av-' + (this.$attrs['avatar-id'] || (Math.floor(Math.random() * 999999)).toString(36));
			this.name = this.$attrs['avatar-name'];
		},
		mounted() {
			this.$_obj = new Avatar('#' + this.domId);
			this.$_obj.fromName(this.name);
		},
		watch: {
			name(newVal) {
				this.$_obj && this.$_obj.fromName(newVal)
			}
		},
		data() {
			return {
				'name': '',
				'domId': '',
			};
		},
		render() {
			return Vue.h("div", {
				id: this.domId,
				innerHTML: `
		    ${svgData}
			<span>${this.name}</span>
		    `
			})
		}
	}
};