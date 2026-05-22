/-
SAL Type 10: Yoneda Lemma
Nat(Hom(a,-), F) ≅ F(a)

The Presheaf is CONTRAVARIANT: map transforms F b → F a along Hom a b.
This matches the Yoneda embedding h_a = Hom(-, a).
-/

namespace SAL

universe u v

structure FinCategory where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : (a : Obj) → Hom a a
  comp : {a b c : Obj} → Hom b c → Hom a b → Hom a c

/-- Contravariant presheaf: map goes F b → F a along Hom a b -/
structure Presheaf (C : FinCategory) where
  F : C.Obj → Type v
  map : ∀ {a b : C.Obj}, C.Hom a b → F b → F a

structure NatTrans {C : FinCategory} (F G : Presheaf C) where
  component : (a : C.Obj) → F.F a → G.F a

def yonedaObj (C : FinCategory) (a : C.Obj) (b : C.Obj) : Type v :=
  C.Hom b a

def yonedaPresheaf (C : FinCategory) (a : C.Obj) : Presheaf C where
  F := yonedaObj C a
  map := λ f g => C.comp g f

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
