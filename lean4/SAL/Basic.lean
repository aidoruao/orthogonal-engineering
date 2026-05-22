/-
SAL Type III: Adjoint Triple
-/

namespace SAL

universe u v

structure Category where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : (a : Obj) → Hom a a
  comp : {a b c : Obj} → Hom b c → Hom a b → Hom a c

structure Functor (C D : Category) where
  onObj : C.Obj → D.Obj
  onHom : {a b : C.Obj} → C.Hom a b → D.Hom (onObj a) (onObj b)

structure AdjointTriple (C D E : Category) where
  L : Functor C D
  M : Functor D E
  R : Functor E D

def triangleIdentity {C D : Category} (L : Functor C D) (R : Functor D C)
    (unit : ∀ (x : C.Obj), C.Hom x (R.onObj (L.onObj x)))
    (counit : ∀ (x : D.Obj), D.Hom (L.onObj (R.onObj x)) x) : Prop :=
  ∀ (x : C.Obj),
    D.comp (counit (L.onObj x)) (L.onHom (unit x)) = D.id (L.onObj x)

inductive SovereignLayer where
  | Supranational | Constitutional | Statutory | Regulatory | Institutional
  deriving Repr, BEq

structure LayerAdjunction (layer : SovereignLayer) where
  upper : Option SovereignLayer
  lower : Option SovereignLayer
  freeFunctor : Bool
  forgetfulFunctor : Bool

end SAL
