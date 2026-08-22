from crewai_tools import YoutubeChannelSearchTool

# `pytube` (used internally by this CrewAI tool) does not support /@handle URLs.
yt_tool = YoutubeChannelSearchTool(
    youtube_channel_handle="https://www.youtube.com/channel/UCNU_lfiiWBdtULKOw6X0Dig"
)
