import Image from "next/image";

/** The approved globe-and-wave mark. The artwork is not altered; it sits on a Stone tile. */
export function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <Image src="/brand/axis-emblem.png" alt="" width={620} height={516} />
    </span>
  );
}

/** The business name, typeset in brand type. Wording follows the business plan: AXIS Environmental, Sustainable Hospitality. */
export function BrandLockup() {
  return (
    <span className="brand-lockup">
      <BrandMark />
      <span className="brand-word">
        <b>AXIS</b>
        <span>Environmental</span>
        <em className="brand-service">Sustainable Hospitality</em>
      </span>
    </span>
  );
}
