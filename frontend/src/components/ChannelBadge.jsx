import { channelIcon } from '../utils/formatters'

export default function ChannelBadge({ channel }) {
  const c = (channel || 'email').toLowerCase()
  return (
    <span className={`badge badge-channel-${c}`}>
      {channelIcon(c)} {c.charAt(0).toUpperCase() + c.slice(1)}
    </span>
  )
}
