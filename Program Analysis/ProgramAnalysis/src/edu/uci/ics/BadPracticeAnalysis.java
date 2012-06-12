package edu.uci.ics;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CatchClause;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.ITypeBinding;
import org.eclipse.jdt.core.dom.InfixExpression;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.TryStatement;
import org.eclipse.jdt.core.dom.InfixExpression.Operator;

import edu.cmu.cs.crystal.AbstractCrystalMethodAnalysis;

public class BadPracticeAnalysis extends AbstractCrystalMethodAnalysis {

	@Override
	public void analyzeMethod(MethodDeclaration m) {
		CodeVisitor visitor = new CodeVisitor();
		m.accept(visitor);
		for (Expression node : visitor.getBadExpr().keySet()) {
			this.reporter.userOut().println(node + ": " + visitor.getBadExpr().get(node));
		}
			
	}

	@Override
	public String getName() {
		return "Check for Bad Practices";
	}

	private class CodeVisitor extends ASTVisitor {

		private static final String STRING_TYPE = "String";
		
		private Map<Expression, String> badExpr = new HashMap<Expression, String>();

		public Map<Expression, String> getBadExpr() {
			return badExpr;
		}

		@Override
		public void endVisit(InfixExpression node) {
			Expression leftOp = node.getLeftOperand();
			Expression rightOp = node.getRightOperand();
			Operator op = node.getOperator();
			
			if (((leftOp.getNodeType() == ASTNode.SIMPLE_NAME &&
					((SimpleName) leftOp).resolveTypeBinding().getName().equals(STRING_TYPE))
					|| (leftOp.getNodeType() == ASTNode.STRING_LITERAL)) &&
					(((rightOp.getNodeType() == ASTNode.SIMPLE_NAME) &&
					((SimpleName) rightOp).resolveTypeBinding().getName().equals(STRING_TYPE))
					|| (rightOp.getNodeType() == ASTNode.STRING_LITERAL)))	
				if (op.equals(Operator.EQUALS) || op.equals(Operator.NOT_EQUALS))
					this.badExpr.put(node, "Comparing Strings with \"==\" or \"!=\".");
		}

		@Override
		public void endVisit(MethodInvocation node) {
			ITypeBinding[] exceptions = node.resolveMethodBinding().getExceptionTypes();
			
			if (exceptions.length > 0) {
				ASTNode exManager = this.getExceptionManager(node);
				
				if (exManager.getNodeType() == ASTNode.METHOD_DECLARATION) {
					MethodDeclaration declMethod = (MethodDeclaration) exManager;
					List parentExceptions = declMethod.thrownExceptions();
					for (ITypeBinding exp : exceptions) {
						int i = 0;
						for (; i < parentExceptions.size(); i++)
							if (((Name) parentExceptions.get(i)).getFullyQualifiedName().contains(exp.getName()))
								break;
						if (i == parentExceptions.size()) {
							// the exception type does not exist in parent method's exception list
							this.badExpr.put(node, "Exception " + exp.getName() + " is not managed.");
						}
					}
				} else {
					TryStatement tryStat = (TryStatement) exManager;
					List catchClauses = tryStat.catchClauses();
					for (ITypeBinding exp : exceptions) {
						int i = 0;
						for (; i < catchClauses.size(); i++) {
							if (((CatchClause) catchClauses.get(i)).getException().getType().resolveBinding().equals(exp))
								break;
						}
						if (i == catchClauses.size()) {
							// the exception type does not exist in try/catch clauses
							this.badExpr.put(node, "Exception " + exp.getName() + " is not managed.");
						}
					}
				}
			}
		}
		
		private ASTNode getExceptionManager(MethodInvocation node) {
			ASTNode parent = node.getParent();
			while (parent.getNodeType() != ASTNode.METHOD_DECLARATION &&
					parent.getNodeType() != ASTNode.TRY_STATEMENT)
				parent = parent.getParent();
			return parent;
		}
	}
}
