export interface Stage { top: number; height: number }

export function getStageTarget(scrollY: number, deltaY: number, viewportHeight: number, stages: Stage[]): number | null {
  let index = 0;
  for (let i = 0; i < stages.length; i++) {
    if (scrollY >= stages[i].top - 2) index = i;
  }
  const stage = stages[index];
  if (!stage || deltaY === 0) return null;
  const end = Math.max(stage.top, stage.top + stage.height - viewportHeight);
  if (deltaY > 0 && index + 1 < stages.length && scrollY >= end - 2) return stages[index + 1].top;
  if (deltaY < 0 && index > 0 && scrollY <= stage.top + 2) {
    const previous = stages[index - 1];
    return Math.max(previous.top, previous.top + previous.height - viewportHeight);
  }
  return null;
}
