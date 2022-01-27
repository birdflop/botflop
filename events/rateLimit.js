module.exports = async (client, info) => {
	client.logger.warn(`Encountered ${info.method} rate limit!`);
};