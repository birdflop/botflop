import { Message } from 'discord.js';
import { analyzeProfile, analyzeTimings } from '@birdflop/analyze';

export async function analyzeMessageLogs(message: Message, words: string[]) {
  // Try finding any timings or spark profile URL in words or content
  let targetUrl: string | undefined;

  for (const word of words) {
    if (
      word.startsWith('https://spark.lucko.me/') ||
      word.startsWith('https://timin') ||
      word.startsWith('https://spigotmc.org/go/timings?url=') ||
      word.startsWith('https://www.spigotmc.org/go/timings?url=')
    ) {
      targetUrl = word;
      break;
    }
  }

  if (!targetUrl) return;

  // Extract ID or handle Spigot message
  if (
    targetUrl.startsWith('https://www.spigotmc.org/go/timings?url=') ||
    targetUrl.startsWith('https://spigotmc.org/go/timings?url=')
  ) {
    await message.reply(
      "❌ Spigot timings have limited information. Switch to Purpur (or Paper) for better timings analysis. All your plugins will be compatible, and if you don't like it, you can easily switch back."
    );
    return;
  }

  let id = '';
  let isProfile = false;
  if (targetUrl.startsWith('https://spark.lucko.me/')) {
    id = targetUrl.replace('https://spark.lucko.me/', '');
    isProfile = true;
  } else if (targetUrl.startsWith('https://timin')) {
    id =
      (
        targetUrl
          .replace('/d=', '/?id=')
          .replace('timin.gs', 'timings.aikar.co')
          .split('#')[0] ?? ''
      ).split('\n')[0] ?? '';
    if (id.includes('/?id=')) {
      id = id.split('/?id=')[1] ?? '';
    }
  }

  if (!id) return;

  const analysisResult =
    id.length < 30 ? await analyzeProfile(id) : await analyzeTimings(id);

  if (!analysisResult) return;

  // Build recommendation summary for automatic message analysis
  const topRecommendations = analysisResult.slice(0, 5);
  let description = isProfile
    ? '## Spark Profile Analysis Recommendations\n'
    : '## Timings Analysis Recommendations\n';

  if (topRecommendations.length === 0) {
    description += "✅ Your server isn't lagging! No performance recommendations found.";
  } else {
    for (const item of topRecommendations) {
      description += `\n**${item.name}**\n${item.value}\n`;
    }
    if (analysisResult.length > 5) {
      description += `\n*Plus ${analysisResult.length - 5} more recommendations. Use \`/analyze\` to view the complete interactive analysis.*`;
    }
  }

  await message.reply({ content: description });
}
