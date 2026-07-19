import type { Member } from "../../api/projects";

export function MemberList({ members }: { members: Member[] }) {
  if (members.length === 0) {
    return <p className="text-sm text-slate-500">No members yet.</p>;
  }

  return (
    <ul className="divide-y divide-slate-200">
      {members.map((member) => (
        <li key={member.user.id} className="flex items-center justify-between py-2 text-sm">
          <div>
            <p className="font-medium text-slate-900">{member.user.name}</p>
            <p className="text-slate-500">{member.user.email}</p>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
            {member.role}
          </span>
        </li>
      ))}
    </ul>
  );
}
