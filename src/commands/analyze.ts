import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  InteractionContextType,
  ButtonInteraction,
  ComponentType,
  MessageFlags,
  ContainerBuilder,
  TextDisplayBuilder,
} from 'discord.js';
import type { Command } from '~/lists/Objects';
import {
  analyzeProfile,
  analyzeTimings,
  collector as submitCollector,
} from '@birdflop/analyze';

export const analyze: Command = {
  description:
    'Analyze Paper timings or Spark profiles to help optimize your server.',
  defer: true,
  cmd: (cmd) =>
    cmd
      .addStringOption((stringOption) =>
        stringOption
          .setName('url')
          .setDescription('The Timings or Profiles URL')
          .setRequired(true)
      )
      .setContexts(InteractionContextType.Guild, InteractionContextType.BotDM),
  async execute(interaction) {
    try {
      const url = interaction.options.getString('url', true);
      let analysisResult;
      let isProfile = false;

      let id;
      if (
        url.startsWith('https://www.spigotmc.org/go/timings?url=') ||
        url.startsWith('https://spigotmc.org/go/timings?url=')
      ) {
        error(
          "❌ Spigot timings have limited information. Switch to Purpur (or Paper) for better timings analysis. All your plugins will be compatible, and if you don't like it, you can easily switch back.",
          interaction,
          true
        );
        return;
      } else if (url.startsWith('https://spark.lucko.me')) {
        id = url.replace('https://spark.lucko.me/', '');
        isProfile = true;
      } else if (url.startsWith('https://timin')) {
        id =
          (
            url
              .replace('/d=', '/?id=')
              .replace('timin.gs', 'timings.aikar.co')
              .split('#')[0] ?? ''
          ).split('\n')[0] ??
          ''.split('/?id=')[1] ??
          '';
      } else {
        error('❌ This is an invalid link.', interaction, true);
        return;
      }

      if (id.length < 30) {
        analysisResult = await analyzeProfile(id);
        try {
          await submitCollector(
            id,
            'https://api.profiler.birdflop.com',
            'spark'
          );
        } catch (err) {
          console.error('Collector error:', err);
        }
      } else {
        analysisResult = await analyzeTimings(id);
        try {
          await submitCollector(
            id,
            'https://api.profiler.birdflop.com',
            'timings'
          );
        } catch (err) {
          console.error('Collector error:', err);
        }
      }

      if (!analysisResult) {
        error('❌ Failed to analyze the provided link.', interaction, true);
        return;
      }

      const rawSuggestions = analysisResult;
      const titleText = isProfile
        ? '## Spark Profile Analysis'
        : '## Timings Analysis';

      let currentPage = 1;
      const itemsPerPage = 12;
      const totalPages = Math.max(
        1,
        Math.ceil(rawSuggestions.length / itemsPerPage)
      );

      const buildContainer = (page: number) => {
        const container = new ContainerBuilder().setAccentColor(0x5865f2);

        // Header section
        container.addTextDisplayComponents((textDisplay) =>
          textDisplay.setContent(
            `${titleText}\nThese are not magic values. Many of these settings have real consequences on your server's mechanics. See [this guide](https://eternity.community/index.php/paper-optimization/) for detailed information on the functionality of each setting.`
          )
        );
        container.addSeparatorComponents((sep) => sep);

        if (rawSuggestions.length === 0) {
          container.addTextDisplayComponents((td) =>
            td.setContent(
              "✅ Your server isn't lagging! No performance recommendations found."
            )
          );
        } else {
          const startIndex = (page - 1) * itemsPerPage;
          const pageSuggestions = rawSuggestions.slice(
            startIndex,
            startIndex + itemsPerPage
          );

          for (const item of pageSuggestions) {
            const content = `**${item.name}**\n${item.value}`;
            const textDisplay = new TextDisplayBuilder().setContent(content);

            const firstBtn = item.buttons?.[0];
            if (firstBtn?.url) {
              container.addSectionComponents((section) =>
                section
                  .addTextDisplayComponents(textDisplay)
                  .setButtonAccessory((btn) =>
                    btn
                      .setURL(firstBtn.url)
                      .setLabel(firstBtn.text || 'Link')
                      .setStyle(ButtonStyle.Link)
                  )
              );
            } else {
              container.addTextDisplayComponents(textDisplay);
            }
          }

          if (totalPages > 1) {
            container.addSeparatorComponents((sep) => sep);
            container.addTextDisplayComponents((td) =>
              td.setContent(`Page ${page} of ${totalPages}`)
            );

            const actionRow =
              new ActionRowBuilder<ButtonBuilder>().addComponents([
                new ButtonBuilder()
                  .setCustomId('analysis_prev')
                  .setEmoji({ name: '⬅️' })
                  .setStyle(ButtonStyle.Secondary)
                  .setDisabled(page === 1),
                new ButtonBuilder()
                  .setCustomId('analysis_next')
                  .setEmoji({ name: '➡️' })
                  .setStyle(ButtonStyle.Secondary)
                  .setDisabled(page === totalPages),
                new ButtonBuilder()
                  .setURL('https://github.com/pemigrade/botflop')
                  .setLabel('Botflop')
                  .setStyle(ButtonStyle.Link),
              ]);

            container.addActionRowComponents(actionRow);
          }
        }

        return container;
      };

      const initialContainer = buildContainer(currentPage);

      const resultinteraction = await interaction.editReply({
        components: [initialContainer],
        flags: MessageFlags.IsComponentsV2,
      });

      if (totalPages > 1) {
        const filter = (i: ButtonInteraction) =>
          i.user.id === interaction.user.id &&
          i.customId.startsWith('analysis_');
        const btnCollector =
          resultinteraction.createMessageComponentCollector<ComponentType.Button>(
            { filter, time: 300000 }
          );

        btnCollector.on('collect', async (i) => {
          await i.deferUpdate();

          if (i.customId === 'analysis_next') {
            currentPage = currentPage >= totalPages ? 1 : currentPage + 1;
          } else if (i.customId === 'analysis_prev') {
            currentPage = currentPage <= 1 ? totalPages : currentPage - 1;
          }

          const updatedContainer = buildContainer(currentPage);
          await i.editReply({
            components: [updatedContainer],
            flags: MessageFlags.IsComponentsV2,
          });
        });

        btnCollector.on('end', () => {
          interaction
            .editReply({ components: [] })
            .catch((err) => console.error(err));
        });
      }
    } catch (err) {
      error(err, interaction);
    }
  },
};
