// $Id$
/* Copyright (c) 2001 The Regents of the University of California through
   E.O. Lawrence Berkeley National Laboratory, subject to approval by the
   U.S. Department of Energy. See files COPYRIGHT.txt and
   cctbx/LICENSE.txt for further details.

   Revision history:
     2001 Jul 02: Merged from CVS branch sgtbx_special_pos (rwgk)
     2001 May 31: merged from CVS branch sgtbx_type (R.W. Grosse-Kunstleve)
     2001-Apr-22 Implementation of ConstructZ2POp() (R.W. Grosse-Kunstleve)
     Apr 2001: SourceForge release (R.W. Grosse-Kunstleve)
 */

#include <memory>
#include <algorithm>
#include <ctype.h> // cannot use cctype b/o non-conforming compilers
#include <cctbx/sgtbx/groups.h>

namespace cctbx { namespace sgtbx {
  namespace lattice {

    const CentringTypeMap* getConventionalCentringType(char Symbol)
    {
      Symbol = toupper(Symbol);
      if (Symbol == 'Q') return 0;
      for (const CentringTypeMap* map = tables::ConventionalCentringTypeMap;
           map->Symbol != '\0';
           map++) {
        if (map->Symbol == Symbol) return map;
      }
      return 0;
    }

    const RotMx& getConventionalZ2PMatrix(int Symbol)
    {
      using namespace tables::ConventionalZ2PMatrices;
      switch (Symbol) {
        case 'P': return PP;
        case 'A': return AP;
        case 'B': return BP;
        case 'C': return CP;
        case 'I': return IP;
        case 'R': return RP;
        case 'H': return HP;
        case 'F': return FP;
        default: break;
      }
      static RotMx null(0);
      return null;
    }

  } // namespace lattice

  char TrOps::getConventionalCentringTypeSymbol() const
  {
    for (const lattice::CentringTypeMap*
         map = lattice::tables::ConventionalCentringTypeMap;
         map->Symbol != '\0';
         map++)
    {
      if (map->nTrs == nVects()) {
        int nMatch = 0;
        int Match[4];
        cctbx_assert(map->nTrs <= sizeof Match / sizeof (*Match));
        int i, j;
        for(i=0;i<map->nTrs;i++) Match[i] = 0;
        for(i=0;i<map->nTrs;i++) {
          for(j=0;j<map->nTrs;j++) {
            if (Match[j] == 0 && map->Trs[i] == m_Vects[j]) {
              Match[j] = 1;
              nMatch++;
              break;
            }
          }
        }
        if (nMatch == map->nTrs) return map->Symbol;
      }
    }
    return '\0';
  }

  ChOfBasisOp TrOps::getConventionalZ2POp(int RBF, int TBF) const
  {
    char ZSymbol = getConventionalCentringTypeSymbol();
    const RotMx& Z2PMatrix = lattice::getConventionalZ2PMatrix(ZSymbol);
    if (!Z2PMatrix.isValid()) return ChOfBasisOp(0, 0);
    return ChOfBasisOp(RTMx(Z2PMatrix.newBaseFactor(RBF), TrVec(TBF)));
  }

  namespace detail {

    class CmpTrVec {
      private:
        CmpiVect m_CmpiVect;
      public:
        CmpTrVec() : m_CmpiVect(3) {}
        bool operator()(const TrVec& a, const TrVec& b) {
          return m_CmpiVect(a.vec().begin(), b.vec().begin());
        }
    };

    bool FirstIsShorter(const af::int3& a, const af::int3& b) {
      for(std::size_t i=0;i<3;i++) {
        if (a[i]) {
          if (fn::absolute(a[i]) > fn::absolute(b[i])) return false;
          return true;
        }
      }
      return true;
    }

    std::auto_ptr<std::vector<TrVec> >
    BuildListTotLTr(const TrOps& LTr, int TBF)
    {
      std::auto_ptr<std::vector<TrVec> > TLT(new std::vector<TrVec>);

      for (int iLTr = 1; iLTr < LTr.nVects(); iLTr++)
      {
        af::int3 nUTr(1,1,1);
        int i;
        for(i=0;i<3;i++) if (LTr[iLTr][i]) nUTr[i] = 2;

        af::int3 UnitTr;
        for (UnitTr[0] = 0; UnitTr[0] < nUTr[0]; UnitTr[0]++)
        for (UnitTr[1] = 0; UnitTr[1] < nUTr[1]; UnitTr[1]++)
        for (UnitTr[2] = 0; UnitTr[2] < nUTr[2]; UnitTr[2]++)
        {
          TrVec V = LTr[iLTr] - TrVec(UnitTr, 1).newBaseFactor(LTr[0].BF());
          V = V.newBaseFactor(TBF);
          int iTLT;
          for (iTLT = 0; iTLT < TLT->size(); iTLT++) {
            if (!af::cmp(CrossProduct((*TLT)[iTLT].vec(), V.vec()), 0)) {
              if (!FirstIsShorter((*TLT)[iTLT].vec(), V.vec())) {
                (*TLT)[iTLT] = V;
              }
              break;
            }
          }
          if (iTLT == TLT->size()) TLT->push_back(V);
        }
      }

      std::sort(TLT->begin(), TLT->end(), CmpTrVec());

      for(std::size_t i=0;i<3;i++) {
        TrVec V(TBF);
        V[i] = TBF;
        TLT->push_back(V);
      }

      return TLT;
    }

  } // namespace detail

  ChOfBasisOp SpaceGroup::ConstructZ2POp(int RBF, int TBF) const
  {
    ChOfBasisOp result;
    SpaceGroup PrimitiveSgOps;
    const int RBF3 = RBF * RBF * RBF;
    std::auto_ptr<std::vector<TrVec> >
    TLT = detail::BuildListTotLTr(m_LTr, RBF);
    int iTLT[3], i;
    af::int9 Basis;
    for (iTLT[0] =           0; iTLT[0] < TLT->size() - 2; iTLT[0]++) {
      for (i=0;i<3;i++) Basis[i * 3 + 0] = (*TLT)[iTLT[0]][i];
    for (iTLT[1] = iTLT[0] + 1; iTLT[1] < TLT->size() - 1; iTLT[1]++) {
      for (i=0;i<3;i++) Basis[i * 3 + 1] = (*TLT)[iTLT[1]][i];
    for (iTLT[2] = iTLT[1] + 1; iTLT[2] < TLT->size();     iTLT[2]++) {
      for (i=0;i<3;i++) Basis[i * 3 + 2] = (*TLT)[iTLT[2]][i];
      int f = RotMx(Basis, RBF).det() * nLTr();
      if (f == RBF3 || -f == RBF3) {
        if (f < 0) for(i=0;i<3;i++) Basis[i * 3] *= -1;
        try {
          result = ChOfBasisOp(RTMx(RotMx(Basis, RBF), TBF)).swap();
          PrimitiveSgOps = ChangeBasis(result);
        }
        catch (const error&) {
          continue;
        }
        if (PrimitiveSgOps.nLTr() == 1) {
          cctbx_assert(result.M().Rpart().det() == nLTr() * RBF3);
          return result;
        }
      }
    }}}
    throw cctbx_internal_error();
  }

  ChOfBasisOp SpaceGroup::getZ2POp(int RBF, int TBF) const
  {
    ChOfBasisOp CBOp = m_LTr.getConventionalZ2POp(RBF, TBF);
    if (CBOp.isValid()) return CBOp;
    return ConstructZ2POp(RBF, TBF);
  }

}} // namespace cctbx::sgtbx
