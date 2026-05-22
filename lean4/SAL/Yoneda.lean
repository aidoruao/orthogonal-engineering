/-
SAL Type 10: Yoneda Lemma
Nat(Hom(a,-), F) ≅ F(a)

Mathematical foundation: Category theory, representable functors
Biblical: John 14:9 — "Anyone who has seen me has seen the Father."
-/

namespace SAL

universe u v

structure FinCategory where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : (a : Obj) → Hom a a
  comp : {a b c : Obj} → Hom b c → Hom a b → Hom a c

structure Presheaf (C : FinCategory) where
  F : C.Obj → Type v
  map : ∀ {a b : C.Obj}, C.Hom a b → F a → F b

structure NatTrans {C : FinCategory} (F G : Presheaf C) where
  component : (a : C.Obj) → F.F a → G.F a

def yonedaObj (C : FinCategory) (a : C.Obj) (b : C.Obj) : Type v :=
  C.Hom b a

def yonedaPresheaf (C : FinCategory) (a : C.Obj) : Presheaf C where
  F := yonedaObj C a
  map := λ f g => C.comp f g

def yonedaLemma {C : FinCategory} {F : Presheaf C} {a : C.Obj}
    (α : NatTrans (yonedaPresheaf C a) F) : F.F a :=
  α.component a (C.id a)

def yonedaInverse {C : FinCategory} {F : Presheaf C} {a : C.Obj}
    (x : F.F a) : NatTrans (yonedaPresheaf C a) F where
  component := λ b f => F.map f x

structure YonedaIsomorphism (C : FinCategory) (F : Presheaf C) (a : C.Obj) where
  toFun : NatTrans (yonedaPresheaf C a) F → F.F a
  invFun : F.F a → NatTrans (yonedaPresheaf C a) F
  leftInv : ∀ α, invFun (toFun α) = α
  rightInv : ∀ x, toFun (invFun x) = x

end SAL
